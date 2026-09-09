client:
	streamlit run frontend/frontend.py --server.address=0.0.0.0 --server.port=8501 &
server:
	uvicorn backend.backend:app --host 0.0.0.0 --port 8000 &
test:
	streamlit run frontend/frontend-v2.py --server.address=0.0.0.0 --server.port=8501 &
kill:
	pkill -f streamlit ; pkill -f uvicorn
