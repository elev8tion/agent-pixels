class PuppeteerPageController implements PageController {
  async getBrowserState() { /* ... */ }
  async clickElement(index: number) { /* ... */ }
  async inputText(index: number, text: string) { /* ... */ }
  async scroll(options: { down: boolean; numPages: number }) { /* ... */ }
  // ... other methods
}
