@property
    def n_workers(self):
        return self.n_processes * self.tabs_per_process
