import hudson.util.Secret

def secret = Secret.fromString("vagrant")
println(secret.getEncryptedValue())
