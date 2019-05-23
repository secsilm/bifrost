source activate bifrost
nohup python app.py > app.out & echo $! > run.pid
