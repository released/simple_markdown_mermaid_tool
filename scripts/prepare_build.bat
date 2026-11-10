@echo off
python "%~dp0prepare_build_identity.py" --module "src/markdown_mermaid_tool/build_info.py"
exit /b %errorlevel%
