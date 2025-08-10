# 运行问答模式（默认）
python main.py

# 批量测试模式
python main.py --mode run

# 更新索引（追加模式）
python main.py --mode update --update-mode append --knowledge-base path/to/new_knowledge.xlsx

# 更新索引（覆盖模式）
python main.py --mode update --update-mode overwrite --knowledge-base path/to/new_knowledge.xlsx

# 第一次构建索引
python main.py --mode update --update-mode overwrite