import hashlib

def generate_sha256_hash(data):
  hasher = hashlib.sha256()
  hasher.update(data.encode()) 
  return hasher.hexdigest()

data = ""
hash_value = generate_sha256_hash(data)
print(f"SHA-256 Hash: {hash_value}")

