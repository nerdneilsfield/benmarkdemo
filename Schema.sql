CREATE TABLE posts (
  post_id integer primary key autoincrement,
  title text not null,
  descrption text,
  content text,
  create_time datetime not null,
  update_time datetime default current_time
);

CREATE TABLE tags (
  tag_id integer primary key autoincrement,
  name text
);

CREATE TABLE post_tags (
  id integer primary key autoincrement,
  post_id int not null,
  tag_id int not null
);