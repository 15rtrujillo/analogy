def compare_text(text1: str, text2: str) -> float:
    """Compares two strings. Returns the similarity as a decimal percent"""

    # Strip whitespace
    text1 = "".join(text1.split())
    text2 = "".join(text2.split())

    longest = lcs(text1, text2)

    return longest / max(len(text1), len(text2))


def lcs(string1: str, string2: str) -> int:
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
    
    return c[m][n]


if __name__ == "__main__":
    print(compare_text("ABCD", "ACBAD"))
