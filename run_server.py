import uvicorn
import sys
import os

if __name__ == "__main__":
    port = 8055
    reload_flag = True
    
    for arg in sys.argv[1:]:
        if arg == "--no-reload":
            reload_flag = False
        elif arg.isdigit():
            port = int(arg)
            
    print(f"Starting Bangladesh Scantling Statutory Compliance Suite on http://127.0.0.1:{port} (reload={reload_flag})")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=reload_flag)
