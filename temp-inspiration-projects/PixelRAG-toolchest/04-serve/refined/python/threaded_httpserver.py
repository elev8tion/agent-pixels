class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
