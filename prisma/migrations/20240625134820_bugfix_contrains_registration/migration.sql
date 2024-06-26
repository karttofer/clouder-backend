-- DropForeignKey
ALTER TABLE "SecretPins" DROP CONSTRAINT "SecretPins_user_id_fkey";

-- DropIndex
DROP INDEX "SecretPins_user_id_key";

-- AlterTable
ALTER TABLE "SecretPins" ADD CONSTRAINT "SecretPins_pkey" PRIMARY KEY ("user_id");
