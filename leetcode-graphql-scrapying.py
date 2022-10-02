import json

import requests
from absl import app
from absl import flags
from absl import logging
from tqdm.auto import tqdm

_DIFFICULTY = flags.DEFINE_multi_integer('difficulty',
                                         default=[1, 2, 3],
                                         help='Difficulty level to include',
                                         lower_bound=1,
                                         upper_bound=3)


def main(argv):
    if len(argv) > 1:
        raise RuntimeError("Unknown arguments")

    query = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    boundTopicId
    title
    titleSlug
    content
    translatedTitle
    translatedContent
    isPaidOnly
    difficulty
    likes
    dislikes
    isLiked
    similarQuestions
    exampleTestcases
    categoryTitle
    contributors {
      username
      profileUrl
      avatarUrl
      __typename
    }
    topicTags {
      name
      slug
      translatedName
      __typename
    }
    companyTagStats
    codeSnippets {
      lang
      langSlug
      code
      __typename
    }
    stats
    hints
    solution {
      id
      canSeeDetail
      paidOnly
      hasVideoSolution
      paidOnlyVideo
      __typename
    }
    status
    sampleTestCase
    metaData
    judgerAvailable
    judgeType
    mysqlSchemas
    enableRunCode
    enableTestMode
    enableDebugger
    envInfo
    libraryUrl
    adminUrl
    challengeQuestion {
      id
      date
      incompleteChallengeCount
      streakCount
      type
      __typename
    }
    __typename
  }
}
"""

    ALGORITHMS_ENDPOINT_URL = "https://leetcode.com/api/problems/algorithms/"
    algorithms_problems_json = requests.get(ALGORITHMS_ENDPOINT_URL).content
    algorithms_problems_json = json.loads(algorithms_problems_json)

    links = []
    for child in algorithms_problems_json["stat_status_pairs"]:
        # Only process free problems
        if not child["paid_only"]:
            question__title_slug = child["stat"]["question__title_slug"]
            question__article__slug = child["stat"]["question__article__slug"]
            question__title = child["stat"]["question__title"]
            frontend_question_id = child["stat"]["frontend_question_id"]
            difficulty = child["difficulty"]["level"]
            if not difficulty in _DIFFICULTY.value:
                continue
            links.append(
                (question__title_slug, difficulty, frontend_question_id,
                 question__title, question__article__slug))

    links = sorted(links, key=lambda x: (x[2]))

    url = 'https://leetcode.com/graphql'

    for title_slug, difficulty, question_id, _, _ in tqdm(links):
        variables = {"titleSlug": title_slug}
        r = requests.post(url, json={'query': query, 'variables': variables})
        if r.status_code == 200:
            res = json.loads(r.text)
            with open(f"json/LC{question_id}.json", "w") as f:
                json.dump(res, f)
        else:
            logging.error('Failed to retrieve %s: %d', title_slug,
                          r.status_code)


if __name__ == '__main__':
    app.run(main)
