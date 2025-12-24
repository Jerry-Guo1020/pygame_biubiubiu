# 导入os模块，用于操作系统相关功能，如文件路径操作
import os

# 获取最高分文件的路径
# 返回当前文件所在目录下的max_score.txt文件路径
def _score_path():
    return os.path.join(os.path.dirname(__file__), "max_score.txt")

# 读取最高分
# 从文件中读取保存的最高分，如果文件不存在或读取失败则返回0
def read_max_score():
    # 获取最高分文件路径
    p = _score_path()
    try:
        # 以只读模式打开文件，使用UTF-8编码
        with open(p, "r", encoding="utf-8") as f:
            # 读取文件内容，去除首尾空白字符，如果为空则默认为"0"，然后转换为整数
            v = int(f.read().strip() or "0")
            # 确保返回值不小于0
            return max(0, v)
    except Exception:
        # 如果读取过程中出现异常，返回0
        return 0

# 保存最高分
# 如果当前分数高于已保存的最高分，则更新保存的最高分
def save_max_score(score):
    try:
        # 读取当前保存的最高分
        cur = read_max_score()
        # 如果当前分数高于已保存的最高分
        if score > cur:
            # 以写入模式打开文件，使用UTF-8编码
            with open(_score_path(), "w", encoding="utf-8") as f:
                # 将分数转换为整数后写入文件
                f.write(str(int(score)))
    except Exception:
        # 如果保存过程中出现异常，忽略错误
        pass

# 将数字分解为百位、十位和个位
# 输入一个数字，返回其百位、十位和个位数字
def cut_number(num):
    try:
        # 将输入转换为整数
        n = int(num)
    except Exception:
        # 如果转换失败，设为0
        n = 0
    # 确保数字不小于0
    if n < 0: n = 0
    # 确保数字不大于999
    if n > 999: n = 999
    # 计算百位数字（取整除以100的余数）
    h = (n // 100) % 10
    # 计算十位数字（取整除以10的余数）
    t = (n // 10) % 10
    # 计算个位数字（取除以10的余数）
    s = n % 10
    # 返回百位、十位、个位数字
    return h, t, s
