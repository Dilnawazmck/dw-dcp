# Standard Library imports

# Third-Party imports
import numpy as np
import pandas as pd

# Local Source Tree imports
from app.utils.constants import (
    MIN_SENTENCE_LENGTH,
    MIN_THRESHOLD,
    UNCLASSIFIED_CATEGORY,
)


def get_similar_theme(data: pd.Series, themes: list, use_model):
    output = []
    fin_list = []
    resp_themes = []
    resp_themes_score = []

    # Convert all sentences to unclassified if the length <= 5 as it can't be correctly classified by the model.
    data = data.apply(
        lambda x: UNCLASSIFIED_CATEGORY if len(x) <= MIN_SENTENCE_LENGTH else x
    )

    embedded_data = use_model(data)
    for item in themes:
        result = np.inner(embedded_data, use_model(item))
        for res in result:
            output.append(res.mean())
        fin_list.append(output.copy())
        output.clear()

    transposed_arr = np.array(fin_list).transpose()
    for i, item in enumerate(transposed_arr):
        if item.max() < MIN_THRESHOLD:
            resp_themes.append(UNCLASSIFIED_CATEGORY)
        else:
            resp_themes.append(themes[item.argmax()][0])
        if resp_themes[i] == UNCLASSIFIED_CATEGORY:
            resp_themes_score.append(-1)
        else:
            resp_themes_score.append(item.max())
    return resp_themes, resp_themes_score
