def have_common_chars(str1, str2):
    # 遍历第一个字符串中的每个字符
    for char in str1:
        # 如果字符出现在第二个字符串中，则返回True
        if char in str2:
            return True
    # 如果没有找到重复字符，则返回False
    return False

# 测试示例
str1 = "hello"
str2 = "wsrsd"

result = have_common_chars(str1, str2)
print("两个字符串是否有重复字符:", result)
