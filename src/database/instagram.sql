CREATE DATABASE instagram;
use instagram;

CREATE TABLE usuario(
    idusuario INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nome varchar(100) NOT NULL,
    senha varchar(100) NOT NULL
);

CREATE TABLE post(
    idpost INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    texto varchar(100) NOT NULL,
    hora varchar(100) NOT NULL,
    idusuario int
);

CREATE TABLE comentario(
    idcomentario INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    texto varchar(100) NOT NULL,
    hora varchar(100) NOT NULL,
    idusuario int
);

CREATE TABLE likes(
    idlikes INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    hora varchar(100) NOT NULL,
    idusuario int,
    idpost int
);

Alter table post add constraint fk_usuario_post foreign key (idusuario) references usuario(idusuario);
Alter table comentario add constraint fk_usuario_comentario foreign key (idusuario) references usuario (idusuario);
Alter table likes add constraint fk_usuario_likes foreign key (idusuario) references usuario(idusuario);
Alter table likes add constraint fk_post_likes foreign key (idpost) references post(idpost);
