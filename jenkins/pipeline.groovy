
def runGitleaks() {
    sh '''
        gitleaks git \
            --report-format json \
            --report-path gitleaks-report.json \
            --redact=100 \
            --exit-code 1 \
            .
    '''
}

def runPylint() {
    sh '''
        make jenkins/Makefile lint
    '''
}

def buildDocker() {
    sh '''
        sh 'make -f jenkins/Makefile docker-build IMAGE_TAG="$BUILD_NUMBER"'
    '''
}

def pushDocker() {
    sh '''
        sh 'make -f jenkins/Makefile docker-push IMAGE_TAG="$BUILD_NUMBER"'
    '''
}

return this