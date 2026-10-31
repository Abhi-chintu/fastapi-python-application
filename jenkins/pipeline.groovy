
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
        make lint
    '''
}

def buildDocker() {
    sh '''
        make docker-build
    '''
}

def pushDocker() {
    sh '''
        make docker-push
    '''
}

return this