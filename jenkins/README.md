# Jenkins configuration

1. Enable build trigger

  <img width="994" height="289" alt="image" src="https://github.com/user-attachments/assets/06b43b0c-b01b-439d-8cd6-13a7284878d7" />

2. Fill in the event actions as shown below (Enable jsonpath for all)

   Variable = event_action, pr_number, pr_base, pr_sha, pr_repo, repo_name, push_ref, push_sha, pr_sha, release_tag, 
   Expression = $.action, $.pull_request.number, $.pull_request.base.ref, $.pull_request.head.sha, $.pull_request.head.repo.full_name, $.repository.full_name, $.ref, $.after, $.pull_request.head.sha, $.release.tag_name,

3. Fill in Header parameters

   <img width="936" height="348" alt="image" src="https://github.com/user-attachments/assets/ea619995-4212-46a8-8bda-912a08743ff7" />

4. Fill in token

   <img width="946" height="225" alt="image" src="https://github.com/user-attachments/assets/edd8ec49-8870-4f54-90cd-5908d285b4e2" />

   <img width="1240" height="474" alt="image" src="https://github.com/user-attachments/assets/5816de3b-3184-439a-8a29-5cb824a85577" />

   to generate this token use github PAT.


5. Optional filter as shown below

   <img width="954" height="330" alt="image" src="https://github.com/user-attachments/assets/8b98300a-dc15-4f52-a21f-5ac857d32e56" />

6. Email notification

   <img width="1235" height="519" alt="image" src="https://github.com/user-attachments/assets/f72bdab0-194a-4949-bc1b-d3ed33896500" />

Add mail id under Default Recipients

# WEBHOOK Configuration

1. Payload URL

   http://<ec2-public-ip>:8080///generic-webhook-trigger/invoke?token=<token_id>

2. Content type

   application/json

3. Select individual events for triiger

   Pushes, Pull request, Releases
