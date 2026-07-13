def forward(self, x):
        return x * self.log_scale.exp()
