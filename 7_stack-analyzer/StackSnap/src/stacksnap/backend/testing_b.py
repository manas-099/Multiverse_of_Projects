
from stacksnap.agent.workflow import analyze_repo
import pprint
if __name__=="__main__":
  respo_url="https://github.com/manas-099/RAG"
  app=analyze_repo()
  response=app.invoke({"repo_url":respo_url})
  print(response)

