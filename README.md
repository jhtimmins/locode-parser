# LOCode Parser

LOCode, an abbreviation of Lines Of Code, parses GitHub repositories and returns reports of the number of lines of code per filetype. This repository is the standalone Lambda function and supporting modules that pull a repository path from a queue, parse the contents, and handle the results.

### Status
In development.

### Versions
The initial version will email the report to the email address of the requesting user. Subsequent versions will show the majority of real of results within the webapp at the time of query.
