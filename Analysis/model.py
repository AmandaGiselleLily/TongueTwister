
"""
Created on Thu Jan 29 15:58:11 2026
@author: vashkani
"""

import torch
import torch.nn as nn

class GRBASPredictor(nn.Module):
    """
    Onset/Offset boundary detection model
    """
    def __init__(
        self,
        asr_model,
        decoder_input_ids,
        ssl_out_dim,
        dropout_concat: float = 0.40,
        lstm_dropout: float = 0.40,
        local_conv_channels: int = 128,   
        lstm_hidden: int = 128,):
        
        super().__init__()
        self.asr_model = asr_model
        self.decoder_input_ids = decoder_input_ids
        self.bottleneck_dim = 120
        self.features_out = ssl_out_dim
        self.asr_weight = nn.Parameter(torch.rand(3), requires_grad=True)

        def make_adapter():
            return nn.Sequential(
                nn.Linear(self.features_out, self.bottleneck_dim),
                nn.LeakyReLU(0.05),
                nn.LayerNorm(self.bottleneck_dim),)

        self.adapter_10 = make_adapter()
        self.adapter_11 = make_adapter()
        self.adapter_12 = make_adapter()

        self.dropout = nn.Dropout(p=float(dropout_concat))

       
        concat_dim = 120  # 120 (ASR only)
        self.local_conv = nn.Sequential(
            nn.Conv1d(concat_dim, local_conv_channels, kernel_size=5, padding=2),
            nn.GELU(),
            nn.BatchNorm1d(local_conv_channels),
            nn.Dropout(p=0.20),
            nn.Conv1d(local_conv_channels, local_conv_channels, kernel_size=3, padding=1),
            nn.GELU(),
            nn.BatchNorm1d(local_conv_channels),)
        
        

        self.downstream_lstm = nn.LSTM(
            input_size=local_conv_channels,            # 128
            hidden_size=lstm_hidden,                   # 64
            num_layers=1, #was 2
            bidirectional=False,
            batch_first=True,
            dropout=float(lstm_dropout),)
        
        bilstm_out_dim = lstm_hidden               # 128 it was==> 2 * lstm_hidden for bi-lstm
        self.onset_head = nn.Linear(bilstm_out_dim, 1, bias=True)
        self.offset_head = nn.Linear(bilstm_out_dim, 1, bias=True)

    @staticmethod
    def _align_time(x: torch.Tensor, T: int) -> torch.Tensor:
        B, Tsrc, D = x.shape
        if Tsrc == T:
            return x
        if Tsrc > T:
            return x[:, :T, :]
        pad_len = T - Tsrc
        last = x[:, -1:, :].repeat(1, pad_len, 1)
        return torch.cat([x, last], dim=1)

    def forward(self, asr_mel_feature, wav, stft_features):
        if asr_mel_feature.dim() == 4 and asr_mel_feature.shape[1] == 1:
            asr_in = asr_mel_feature.squeeze(1)
        else:
            asr_in = asr_mel_feature

        B = asr_in.shape[0]
        T = stft_features.shape[2]

        dec_ids = self.decoder_input_ids
        if dec_ids.shape[0] != B:
            dec_ids = dec_ids.repeat(B, 1)
        asr_out = self.asr_model(asr_in, decoder_input_ids=dec_ids, output_hidden_states=True)
        ha = asr_out.encoder_hidden_states
        asr_new = torch.stack(
            [
                self.adapter_10(ha[-1]),
                self.adapter_11(ha[-2]),
                self.adapter_12(ha[-3]),],
            dim=-1,)                                                      # (B,Tasr,120,3)
        w_asr = nn.functional.softmax(self.asr_weight, dim=0).view(3, 1)
        asr_x = torch.matmul(asr_new, w_asr).squeeze(-1)       # (B,Tasr,120)
        asr_x = self._align_time(asr_x, T)

        x = asr_x                                             # (B,T,120)
        x = self.dropout(x)

        # ---- local-context CNN expects (B,C,T) -------------------------------
        x = x.transpose(1, 2)                                  # (B,120,T)
        x = self.local_conv(x)                                 # (B,128,T)
        x = x.transpose(1, 2)                                  # (B,T,128)
        # ----------------------------------------------------------------------

        x, _ = self.downstream_lstm(x)                         # (B,T,128)
        onset_logits = self.onset_head(x).squeeze(-1)          # (B,T)
        offset_logits = self.offset_head(x).squeeze(-1)        # (B,T)
        return onset_logits, offset_logits



