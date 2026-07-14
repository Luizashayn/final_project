#!/bin/bash
cd /Users/luiza/Desktop/final_project
/Users/luiza/Desktop/final_project/venv/bin/python save_data.py >> logs/save_data.log 2>&1
/Users/luiza/Desktop/final_project/venv/bin/python load_to_db.py >> logs/load_to_db.log 2>&1
