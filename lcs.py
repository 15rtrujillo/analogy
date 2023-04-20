def compare_text(text1: str, text2: str) -> tuple[float, list[list[int]]]:
    """Compares two strings. Returns the similarity as a decimal percent"""

    # Strip whitespace
    #text1 = "".join(text1.split())
    #text2 = "".join(text2.split())

    longest, c = lcs(text1, text2)

    return longest / max(len(text1), len(text2)), c


def compare_words(text1: str, text2: str) -> tuple[float, list[list[int]]]:
    """Compares the words in two strings. Returns the similarity as a decimal percent"""
    # Split on whitespace to get "words"
    words1 = text1.split(" ")
    words2 = text2.split(" ")

    longest, c = lcs(words1, words2)

    return longest / max(len(text1), len(text2)), c


def lcs(string1: str | list[str], string2: str | list[str]) -> tuple[int, list[list[int]]]:
    """Get the longest common subsequence length between two strings"""
    m = len(string1)
    n = len(string2)

    # Create a 2-dimensional array using the string sizes for dimensions
    c: list[list[int]] = [[0] * (n + 1) for _ in range(m + 1)]

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


def transpose_c(c: list[list[int]]) -> list[list[int]]:
    x = len(c[0])
    y = len(c)

    new_c: list[list[int]] = [[0] * y for _ in range(x)]

    for i in range(y):
        for j in range(x):
            new_c[j][i] = c[i][j]

    return new_c


def get_diff(c: list[list[int]], string1: str | list[str], string2: str | list[str]) -> str:
    i = len(string1) - 1
    j = len(string2) - 1
    diff: list[str] = list()
    while i >= 0 and j >= 0:
        if string1[i] == string2[j]:
            diff.append(string1[i])
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or c[i][j-1] >= c[i-1][j]):
            diff.append("+" + string2[j])
            j -= 1
        elif i > 0 and (j == 0 or c[i][j-1] < c[i-1][j]):
            diff.append("-" + string1[i])
            i -= 1
        else:
            break
    diff.reverse()
    return "".join(diff)


if __name__ == "__main__":
    diff, c = compare_text("ABCD\n", "ACBAD")
    print(diff)
    print(get_diff(c, "ABCD\n", "ACBAD"))
