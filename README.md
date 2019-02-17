# codeline

using `git blame` and `svn blame` to calculate code line contribution summary.


    Usage: codeline [OPTIONS]

    Options:
        --file-ext TEXT    File extension to be counted  [required]
        --ignore-dir TEXT  dir to be ignored, Unix shell-style wildcards
    
    Example:
    
        codeline --file-ext py \
                    --file-ext md \
                    --ignore-dir 'codeline/*' \
                    --ignore-dir '*/test/*'
                    
    Output:
    
        +-------------------+------------+--------+
        | author            | line count |  radio |
        +-------------------+------------+--------+
        | oylbin            |        285 | 94.68% |
        | Not Committed Yet |         16 |  5.32% |
        +-------------------+------------+--------+