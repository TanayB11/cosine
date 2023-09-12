from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Button, Input, Rule, Markdown
from textual.widget import Widget
from textual.reactive import reactive
from server.main import app as server
from cosine import upload, search, tabulate_search_results
from dotenv import load_dotenv
import os

class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("r", "reindex_vault", "Reindex the vault (slow)")]
    CSS_PATH = "cosine_ui.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Input(placeholder="How does backpropagation work?", id="search_query")
        yield Button.success("Search", id="search")
        yield Rule()
        yield Markdown("", id="search_result")

        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_reindex_vault(self) -> None:
        vault_dir = os.getenv("VAULT_PATH")
        upload(vault_dir)

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id

        if button_id == "search":
            query = self.query_one("#search_query").value
            result = tabulate_search_results(search(query))
            self.query_one("#search_result").update(result)

if __name__ == "__main__":
    load_dotenv()
    client = StopwatchApp()
    client.run()
