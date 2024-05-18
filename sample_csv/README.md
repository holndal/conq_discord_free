# csv読み方

## leader.csv
統率値を取得

`(disocrd user id),(value)`

sample:`_dgn_,700`

## level.csv
初心者とベテランを区別したいという要望があり追加。PT編成時に初心者だけにならないように追加した。ぶっちゃけ使わなくても良い

`(disocrd user id),(TRUE/FALSE)`

sample:`_dgn_,TRUE`

## member.csv
discordのユーザー名だと誰かわかりづらいので、nicknameやdisplay_nameに変換する為に使用

sample: `_dgn_,デス・ｘ・ガン`

## unit.csv

`main.py` で、unitsの宣言の順番に
1. 兵団所有。統率軍魂無し
2. 兵団所有。統率軍魂有り(レア)
3. 兵団所有。統率軍魂有り(エピック)

sample: `_dgn_,1,,3,(省略)`

unitsは
`忠誠長槍兵,武衛鉄人兵,遼東重甲兵,(省略)`なので

- 忠誠: 1(兵団所有)
- 武衛: 空欄(未所有)
- 遼東: 3(兵団所有(エピ統率軍魂))

となる。

## スプレッドシートでの使い方

`=IMPORTDATA(URL, ",", "ja-jp")`
で使う。

[サンプルのスプレッドシート](https://docs.google.com/spreadsheets/d/1tQQOymUzl7FnRdouxhITo_YetuSBKO1LnPTnuZbqSLI/edit?usp=sharing)で見ると良い

とりあえず適当なスプレッドシート開いて

`=IMPORTDATA("https://dl.dropboxusercontent.com/scl/fi/fvhyg8eypp5peuok9laq0/member.csv?rlkey=c9vmol04qizvdpubu47ndyoek&st=69np5oul&dl=0", ",", "ja-jp")`

で何が起こるか見ると良いかもしれない。(member.csv)

| A | B |
| ---- | ---- |
| `_dgn_` | `デス・ｘ・ガン` |

とかになると思う
