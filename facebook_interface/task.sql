/*
 Navicat Premium Data Transfer

 Source Server         : fb
 Source Server Type    : SQLite
 Source Server Version : 3030001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3030001
 File Encoding         : 65001

 Date: 09/06/2022 17:09:45
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS "task";
CREATE TABLE "task" (
  "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "profile_id" text NOT NULL,
  "nickname" TEXT,
  "like_link" text,
  "group_link" text,
  "media_path" text,
  "status" text NOT NULL,
  "info" integer NOT NULL DEFAULT 1
);

-- ----------------------------
-- Records of task
-- ----------------------------
INSERT INTO "task" VALUES (12, 123123, 'qiqi', NULL, NULL, NULL, '{"添加推荐好友": 0}', 1);
INSERT INTO "task" VALUES (13, '2c996b3780da3aea0180df2acc854d0c', 'Sheridan', 'https://www.facebook.com/Teapot-Woye-101842359168022/?ref=pages_you_manage', NULL, 'Q:\fb_task\05\20\2022052012', '{"添加推荐好友": 1, "确认好友请求": 0, "邀请好友点赞": 0, "分享公共主页": 0, "加入指定公共小组": 0, "个人主页发表帖子": 0, "公共主页发表帖子": 0, "小组发表帖子": 0}', 1);

-- ----------------------------
-- Auto increment value for task
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 13 WHERE name = 'task';

PRAGMA foreign_keys = true;
