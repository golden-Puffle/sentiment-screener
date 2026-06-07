@echo off
cd C:\Users\monis\OneDrive\Desktop\sentiment_screener
call venv\Scripts\activate
python main.py
git add data/screener.db
git commit -m "data: daily sentiment and price update"
git push