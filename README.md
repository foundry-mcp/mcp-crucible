# mcp_crucible

MCP server for the Crucible Python Client

#### Usage with Claude Code: 
1. Clone this repository 
2. Install and set up Claude Code:
3. Create a virtual environment from the requirements file
4. Connect Claude Code to the Crucible MCP server using stdio
<br>
   ``` claude mcp add --transport stdio crucible-mcp --env CRUCIBLE_API_KEY={your-api-key} --env CRUCIBLE_API_URL=https://crucible.lbl.gov/testapi2 -- uv run python crucible_mcp_server.py ```
<br>
You can create or retrieve your crucible api key by navigating to https://crucible.lbl.gov/testapi2/user_apikey and logging in with your ORCID credentials
