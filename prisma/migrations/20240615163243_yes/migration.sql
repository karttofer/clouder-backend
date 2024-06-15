/*
  Warnings:

  - A unique constraint covering the columns `[message_id]` on the table `UserThreads` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `created_at` to the `UserThreads` table without a default value. This is not possible if the table is not empty.
  - Added the required column `message_id` to the `UserThreads` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "UserThreads" ADD COLUMN     "created_at" INTEGER NOT NULL,
ADD COLUMN     "message_id" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "UserThreads_message_id_key" ON "UserThreads"("message_id");
