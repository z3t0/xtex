import sys

def read_markdown(req_name):
    with open(req_name, 'r') as f:
        return f.readlines()


def main():
   req_file = sys.argv[1]

   if not req_file:
       raise Error("req file missing")

   req = read_markdown(req_file)

   print(req)
    
main()
