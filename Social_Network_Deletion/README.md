# DEMO步驟
1. git clone 此 project
2. cd social_network_deletion
3. otree collectstatic
3. otree devserver
4. 輸入 http://localhost:8000/ 

# 第一次操作的時候
## 下載整個 project
git clone https://github.com/uuuChen/social_network_version_2.git
git remote add https://github.com/uuuChen/social_network_version_2

# 上傳
git add . <br>
git commit -m "version_name" <br>
git push origin master <br>

# 更新
## 保留自己的程式碼，同時更新
git stash <br>
git pull origin master <br>
git stash pop <br>

## 強制更新
git reset --hard <br>
git pull origin master <br>
