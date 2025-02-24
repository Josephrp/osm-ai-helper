python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[demo]"
python -m pip install --upgrade streamlit
sudo apt-get update && sudo apt-get install libgl1 -y
