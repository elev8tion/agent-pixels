@property
    def ports(self) -> list[int]:
        return [self.base_port + i for i in range(self.num_instances)]
