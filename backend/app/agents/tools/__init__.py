from .scrape_website import ScrapeWebsiteTool
from .write_notion import WriteNotionTool
from .send_email import SendEmailTool
from .read_pdf import ReadPDFTool
from .create_task import CreateTaskTool
from .search_google import SearchGoogleTool
from .run_python import RunPythonTool
from .summarize_text import SummarizeTextTool
from .calendar_tool import CalendarTool
from .file_manager import FileManagerTool
from .codebase_explorer import CodebaseExplorerTool

ALL_TOOLS = [
    ScrapeWebsiteTool(),
    WriteNotionTool(),
    SendEmailTool(),
    ReadPDFTool(),
    CreateTaskTool(),
    SearchGoogleTool(),
    RunPythonTool(),
    SummarizeTextTool(),
    CalendarTool(),
    FileManagerTool(),
    CodebaseExplorerTool(),
] 