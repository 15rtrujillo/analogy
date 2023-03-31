def compare_text(text1: str, text2: str) -> tuple[float, list[list[int]]]:
    """Compares two strings. Returns the similarity as a decimal percent"""

    # Strip whitespace
    text1 = "".join(text1.split())
    text2 = "".join(text2.split())

    longest, c = lcs(text1, text2)

    return longest / max(len(text1), len(text2)), c


def compare_words(text1: str, text2: str) -> tuple[float, list[list[int]]]:
    """Compares the words in two strings. Returns the similarity as a decimal percent"""
    # Split on whitespace to get "words"
    words1 = text1.split()
    words2 = text2.split()

    longest, c = lcs(words1, words2)

    return longest / max(len(text1), len(text2)), c


def lcs(string1: str | list[str], string2: str | list[str]) -> tuple[int, list[list[int]]]:
    """Get the longest common subsequence length between two strings"""
    m = len(string1)
    n = len(string2)
    c: list[list[int]] = list()

    # Fill in the 2D array
    # The array needs to be m + 1 x n + 1
    # Since range is uninclusive, we have to add two
    for i in range(m + 1):
        c.append(list())
        for j in range(n + 1):
            c[i].append(0)

    for i in range(m + 1):
        c[i][0] = 0
    
    for i in range(n + 1):
        c[0][i] = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if string1[i - 1] == string2[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
            else:
                c[i][j] = max(c[i][j - 1], c[i - 1][j])
    
    return c[m][n], c


def get_diff(c: list[list[int]], string1: str | list[str], string2: str | list[str], i: int = 0, j: int = 0) -> str:
    diff = ""
    if i >= 0 and j >= 0 and string1[i] == string2[j]:
        diff += get_diff(c, string1, string2, i-1, j-1)
        diff += "  " + string1[i]
    elif j > 0 and (i == 0 or c[i][j-1] >= c[i-1][j]):
        diff += get_diff(c, string1, string2, i, j-1)
        diff += "+ " + string2[j]
    elif i > 0 and (j == 0 or c[i][j-1] < c[i-1][j]):
        diff += get_diff(c, string1, string2, i-1, j)
        diff += "- " + string1[i]
    else:
        diff += ""
    return diff


if __name__ == "__main__":
    print(compare_text("ABCD", "ACBAD"))
