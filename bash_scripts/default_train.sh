python ./main.py \
    --learning_rate 0.001 \
    --discount_factor 0.99 \
    --env_name LunarLander-v2 \
    --iterations 1000 \
    --episodes 64 \
    --batch_size 32 \
    --n_threads 4 \
    --max_replay 500000
