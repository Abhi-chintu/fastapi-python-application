
def runGitleaks() {
    sh '''
        gitleaks git \
            --report-format json \
            --report-path gitleaks-report.json \
            --redact=100 \
            --exit-code 1 .
    '''
}

def runPylint() {
    sh '''
        make -f jenkins/Makefile lint
    '''
}

def buildDocker() {
    sh '''
        make -f jenkins/Makefile docker-build IMAGE_TAG="$IMAGE_TAG"
    '''
}

def pushDocker() {
    sh '''
        make -f jenkins/Makefile docker-push IMAGE_TAG="$IMAGE_TAG"
    '''
}

return this
