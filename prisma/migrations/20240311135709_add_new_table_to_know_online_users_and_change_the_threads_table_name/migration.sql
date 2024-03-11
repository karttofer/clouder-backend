/*
  Warnings:

  - You are about to drop the `Threads` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "Threads" DROP CONSTRAINT "Threads_user_id_fkey";

-- DropTable
DROP TABLE "Threads";

-- CreateTable
CREATE TABLE "LoggedUsers" (
    "user_id" TEXT NOT NULL,
    "isLogged" BOOLEAN NOT NULL
);

-- CreateTable
CREATE TABLE "SecretPins" (
    "user_id" TEXT NOT NULL,
    "pin" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "UserThreads" (
    "thread_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "thread_name" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "LoggedUsers_user_id_key" ON "LoggedUsers"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "SecretPins_user_id_key" ON "SecretPins"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "UserThreads_thread_id_key" ON "UserThreads"("thread_id");

-- AddForeignKey
ALTER TABLE "LoggedUsers" ADD CONSTRAINT "LoggedUsers_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SecretPins" ADD CONSTRAINT "SecretPins_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserThreads" ADD CONSTRAINT "UserThreads_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
