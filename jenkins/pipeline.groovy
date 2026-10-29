boolean isFeatureBranchPush(String ref) {
    return ref?.startsWith('refs/heads/') && ref != 'refs/heads/master'
}

boolean isMergedMasterPullRequest(String action, String baseRef, String merged) {
    return action == 'closed' &&
        baseRef == 'master' &&
        merged?.toBoolean()
}

String checkoutRef(String ref, String isMergedPullRequest) {
    return isMergedPullRequest == 'true' ? 'refs/heads/master' : ref
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
            set -euo pipefail
            aws ecr get-login-password --region '${awsRegion}' |
                docker login --username AWS --password-stdin '${ecrRegistry}'
            make -f jenkins/Makefile docker-push ECR_REGISTRY='${ecrRegistry}' IMAGE_TAG='${imageTag}'
        """
    }
}
