boolean shouldRunCI(
    String eventType,
    String action,
    String baseRef,
    String headSha,
    String ref,
    String reviewState,
    String reviewCommit,
    String commitSha
) {
    if (eventType == 'push') {
        return ref?.startsWith('refs/heads/') &&
            ref != 'refs/heads/master' &&
            isCommitSha(commitSha)
    }

    if (eventType == 'pull_request') {
        return baseRef == 'master' &&
            action in ['opened', 'reopened', 'synchronize', 'ready_for_review'] &&
            isCommitSha(headSha)
    }

    return shouldPublish(
        eventType,
        action,
        baseRef,
        headSha,
        reviewState,
        reviewCommit
    )
}

boolean shouldPublish(
    String eventType,
    String action,
    String baseRef,
    String headSha,
    String reviewState,
    String reviewCommit
) {
    return eventType == 'pull_request_review' &&
        action == 'submitted' &&
        reviewState == 'approved' &&
        baseRef == 'master' &&
        isCommitSha(headSha) &&
        reviewCommit == headSha
}

boolean isCommitSha(String sha) {
    return sha != null &&
        sha != '0000000000000000000000000000000000000000' &&
        sha ==~ /(?i)[0-9a-f]{40}/
}

String checkoutSha(String eventType, String commitSha, String headSha) {
    return eventType == 'push' ? commitSha : headSha
}

String imageTag(String prNumber, String headSha) {
    if (!(prNumber ==~ /[0-9]+/) || !isCommitSha(headSha)) {
        throw new IllegalArgumentException('Cannot create an image tag without a valid PR number and commit SHA.')
    }
    return "pr-${prNumber}-${headSha.take(7).toLowerCase()}"
}

void buildImages(String ecrRegistry, String imageTag) {
    sh "make -f jenkins/Makefile docker-build ECR_REGISTRY='${ecrRegistry}' IMAGE_TAG='${imageTag}'"
}

void pushImages(
    String awsRegion,
    String ecrRegistry,
    String imageTag,
    String credentialsId
) {
    withCredentials([[
        $class: 'AmazonWebServicesCredentialsBinding',
        credentialsId: credentialsId
    ]]) {
        sh """
            set -eu
            aws ecr get-login-password --region '${awsRegion}' |
                docker login --username AWS --password-stdin '${ecrRegistry}'
            make -f jenkins/Makefile docker-push ECR_REGISTRY='${ecrRegistry}' IMAGE_TAG='${imageTag}'
        """
    }
}
