from azure.devops.connection import Connection
from azure.devops.v6_0.git import GitClient, GitPullRequestSearchCriteria, GitPullRequest
from msrest.authentication import BasicAuthentication

# Submits all the pull_requests within a repository for the downstream update method calls.
# Iterator is used to loop over each pull_request & pass the active pull requests for completion in order of creation.
# Todo: There is a caviet here ! For cases where we do not want to merge a PR X before PR Y is completed, there is no standard logic established for the same.
def submit_pullrequest_forapproval(
    repository_id,
    pull_request_approval,
    devops_git_client):

    if(len(pull_request_approval) > 0):

        print(f'Starting pull request auto-approval sequence for {len(pull_request_approval)} pull requests.')

        for pull_request in pull_request_approval:

            print(f'Starting auto-approval & merge of PR Id:{pull_request.pull_request_id}')

            update_pullrequest_status(
                repository_id,
                pull_request,
                devops_git_client)

            print(f'Completed auto-approval & merge of PR Id:{pull_request.pull_request_id}')

# Updates the current iterated pull_request status to completed & merges to target branch
def update_pullrequest_status(
    repository_id,
    pull_request,
    devops_git_client):

    git_pr_status = GitPullRequest(
        status='completed',
        last_merge_source_commit=pull_request.last_merge_source_commit)

    if(pull_request is not None):

        devops_git_client.update_pull_request(
            git_pr_status,
            repository_id,
            pull_request.pull_request_id)

# Main script entry point.
# Please set the below mentioned variables before starting script execution.
# Run this command on your machine/env before script execution: pip install azure-devops
# Make sure you are running python version 2.x +
personal_access_token = '{Enter PAT token}'
organization_url = '{Enter the Devops organization url}'
repository_name = '{Enter repository name}'
project_name = '{Enter team project name}'

shared_credentials = BasicAuthentication('', personal_access_token)

devops_connection = Connection(base_url=organization_url, creds=shared_credentials)

print(f'Established secure connection with Azure DevOps instance {organization_url}')

devops_git_clientsvc = devops_connection.clients.get_git_client()

devops_repositories = devops_git_clientsvc.get_repositories()

print(f'Found {len(devops_repositories)} repositories.')

search_criteria = GitPullRequestSearchCriteria()

target_repository = list(filter(lambda x: (x.name == repository_name), devops_repositories))

target_repository_pullrequests = sorted(devops_git_clientsvc.get_pull_requests(
    target_repository[0].id,
    search_criteria), key=lambda x: x.creation_date, reverse=False)

submit_pullrequest_forapproval(
    target_repository[0].id,
    target_repository_pullrequests,
    devops_git_clientsvc)
