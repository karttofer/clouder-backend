/*
  Warnings:

  - You are about to drop the column `UserImage` on the `User` table. All the data in the column will be lost.
  - You are about to drop the column `google_picture_src` on the `User` table. All the data in the column will be lost.
  - You are about to drop the `LoggedUsers` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `UserThreads` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "LoggedUsers" DROP CONSTRAINT "LoggedUsers_user_id_fkey";

-- DropForeignKey
ALTER TABLE "UserThreads" DROP CONSTRAINT "UserThreads_user_id_fkey";

-- AlterTable
ALTER TABLE "User" DROP COLUMN "UserImage",
DROP COLUMN "google_picture_src",
ADD COLUMN     "user_completed_registration" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "user_image" TEXT;

-- DropTable
DROP TABLE "LoggedUsers";

-- DropTable
DROP TABLE "UserThreads";
