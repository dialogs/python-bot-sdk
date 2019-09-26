import copy
import time
import unittest
import grpc
from dialog_api import peers_pb2, messaging_pb2, definitions_pb2
from dialog_bot_sdk import interactive_media
from dialog_api.peers_pb2 import PEERTYPE_PRIVATE
from mock import patch

from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk.utils.get_media import get_webpage


class FakeMessage:
    def __init__(self, mid):
        self.mid = mid
        self.date = int(time.time() - 1000)


class MyTestCase(unittest.TestCase):

    test_file = "./files/test.png"
    test_image = test_file
    test_video = "./files/test.mov"
    test_audio = "./files/test.mp3"

    bot = DialogBot.get_secure_bot(
        '',                               # bot endpoint from environment
        grpc.ssl_channel_credentials(),             # SSL credentials (empty by default!)
        ''  # bot token from environment
    )

    outpeer = peers_pb2.OutPeer(type=PEERTYPE_PRIVATE, id=0, access_hash=0)
    mid = definitions_pb2.UUIDValue(msb=0, lsb=0)
    msg_content = messaging_pb2.MessageContent()
    msg_content.textMessage.text = "Hello"
    group = [interactive_media.InteractiveMediaGroup(
        [
            interactive_media.InteractiveMedia(
                1,
                interactive_media.InteractiveMediaButton("Yes", "Да")
            ),
            interactive_media.InteractiveMedia(
                2,
                interactive_media.InteractiveMediaButton("No", "Нет")
            ),
        ]
    )]
    msg_content_with_group = copy.deepcopy(msg_content)
    group[0].render(msg_content_with_group.textMessage.media.add())
    doc_msg = messaging_pb2.DocumentMessage(
        file_id=0,
        access_hash=0,
        file_size=60,
        name=""
    )

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    def test_send_message(self, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_message(None, "hello"))

        with self.assertRaises(AttributeError):
            self.assertRaises(self.bot.messaging.send_message(None, ""))

        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        self.bot.messaging.send_message(self.outpeer, "Hello")

        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

        self.bot.messaging.send_message(self.outpeer, "Hello", self.group)

        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('dialog_bot_sdk.messaging.Messaging._update_message')
    def test_update_message(self, update):
        message = FakeMessage(self.mid)

        self.bot.messaging.update_message(message, "Hello")

        self.assertTrue(isinstance(update.call_args.args[0], messaging_pb2.RequestUpdateMessage))

        self.bot.messaging.update_message(message, "Hello", self.group)

        args = update.call_args.args[0]
        self.assertTrue(isinstance(args, messaging_pb2.RequestUpdateMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    @patch('dialog_bot_sdk.uploading.Uploading.upload_file')
    def test_send_file(self, upload, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_file(None, ""))
        upload.return_value = self.doc_msg
        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        self.bot.messaging.send_file(self.outpeer, self.test_file)
        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    def test_send_media(self, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_media(None, ""))

        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        media = [get_webpage("dlg.im")]

        self.bot.messaging.send_media(self.outpeer, media)
        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    @patch('dialog_bot_sdk.uploading.Uploading.upload_file')
    def test_send_image(self, upload, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_image(None, ""))
        with self.assertRaises(IOError):
            self.assertRaises(self.bot.messaging.send_image("peer", ""))

        upload.return_value = self.doc_msg
        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        with self.assertRaises(IOError):
            self.bot.messaging.send_image(self.outpeer, self.test_audio)

        self.bot.messaging.send_image(self.outpeer, self.test_image)
        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    @patch('dialog_bot_sdk.uploading.Uploading.upload_file')
    def test_send_audio(self, upload, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_audio(None, ""))
        with self.assertRaises(IOError):
            self.assertRaises(self.bot.messaging.send_audio("peer", ""))

        upload.return_value = self.doc_msg
        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        with self.assertRaises(IOError):
            self.bot.messaging.send_audio(self.outpeer, self.test_image)

        self.bot.messaging.send_audio(self.outpeer, self.test_audio)
        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    @patch('dialog_bot_sdk.uploading.Uploading.upload_file')
    def test_send_video(self, upload, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.send_video(None, ""))
        with self.assertRaises(IOError):
            self.assertRaises(self.bot.messaging.send_video("peer", ""))
        upload.return_value = self.doc_msg
        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        with self.assertRaises(IOError):
            self.bot.messaging.send_video(self.outpeer, self.test_image)

        self.bot.messaging.send_video(self.outpeer, self.test_video)
        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('random.randint')
    @patch('dialog_bot_sdk.messaging.Messaging._send_message')
    @patch('dialog_bot_sdk.entity_manager.EntityManager.get_outpeer')
    def test_reply(self, get_outpeer, send, rnd):
        self.assertIsNone(self.bot.messaging.reply(None, ""))

        get_outpeer.return_value = self.outpeer
        rnd.return_value = 1

        self.bot.messaging.reply(self.outpeer, [self.mid])

        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

        self.bot.messaging.reply(self.outpeer, [self.mid], "hello", self.group)

        self.assertTrue(isinstance(send.call_args.args[0], messaging_pb2.RequestSendMessage))

    @patch('dialog_bot_sdk.messaging.Messaging._load_history')
    def test_load_message_history(self, load):
        self.assertIsNone(self.bot.messaging.load_message_history(None))
        self.bot.messaging.load_message_history(self.outpeer)
        self.assertTrue(isinstance(load.call_args.args[0], messaging_pb2.RequestLoadHistory))
        self.bot.messaging.load_message_history(self.outpeer, 1)
        self.assertTrue(isinstance(load.call_args.args[0], messaging_pb2.RequestLoadHistory))
        self.bot.messaging.load_message_history(self.outpeer, 1, messaging_pb2.LISTLOADMODE_BACKWARD)
        self.assertTrue(isinstance(load.call_args.args[0], messaging_pb2.RequestLoadHistory))
        self.bot.messaging.load_message_history(self.outpeer, 1, messaging_pb2.LISTLOADMODE_BACKWARD, 1)
        self.assertTrue(isinstance(load.call_args.args[0], messaging_pb2.RequestLoadHistory))

    @patch('dialog_bot_sdk.messaging.Messaging._delete')
    def test_delete(self, delete):
        self.bot.messaging.delete([self.mid])
        self.assertTrue(isinstance(delete.call_args.args[0], messaging_pb2.RequestDeleteMessageObsolete))

    @patch('dialog_bot_sdk.messaging.Messaging._read')
    def test_read(self, read):
        self.bot.messaging.messages_read(self.outpeer, 0)
        self.assertTrue(isinstance(read.call_args.args[0], messaging_pb2.RequestMessageRead))


if __name__ == '__main__':
    unittest.main()