import datetime
from uuid import uuid4

from Crypto.Hash import SHA3_256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ballot.merkle.merkle_tool import MerkleTools
from ballot.models import Vote, Block, VoteBackup
import time
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


@login_required(login_url='/')
def submit_vote(request):
    if request.method == "POST":
        private_key_input = request.POST.get('private-key-input')
        vote = request.POST.get('vote-input')
        # timestamp = datetime.datetime.now().timestamp()
        timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))
        ballot = f"{request.user.id}|{vote}|{timestamp}"

        print("\nballot : ", ballot)
        signature = ""

        if Vote.objects.filter(user=request.user).exists():
            messages.warning(request, 'You have already voted.')
            return render(request, 'create_vote.html')

        # verify keys
        try:
            # Create signature

            priv_key = ECC.import_key(private_key_input)
            hash_string = SHA3_256.new(ballot.encode('utf-8'))
            signature = DSS.new(priv_key, 'fips-186-3').sign(hash_string)
            print('\nsignature: ', signature.hex())

            public_key = ECC.import_key(request.user.user_public_key)
            verifier = DSS.new(public_key, 'fips-186-3')
            verifier.verify(hash_string, signature)

            status = 'The ballot is signed successfully.'
            error = False

        except Exception as e:
            status = 'The key is not registered.'
            error = True
            print("not matched")
            print(e)
            messages.warning(request, str(e))
            return render(request, 'create_vote.html')

        # get block id
        try:
            block_id = int(Vote.objects.last().block_id)
            block_id += 1
        except:
            block_id = 1

        # create vote object
        v_id = str(uuid4())
        v_timestamp = _get_timestamp()
        vote_obj = Vote.objects.create(id=v_id, user=request.user, vote=vote, timestamp=v_timestamp, block_id=block_id)
        VoteBackup.objects.create(id=v_id, user=request.user, vote=vote, timestamp=v_timestamp, block_id=block_id)

        context = {
            'ballot': ballot,
            'signature': signature,
            'status': status,
            'error': error,
            'vote_id': vote_obj.id
        }

        return render(request, 'vote_status.html', context)
    else:
        return render(request, 'create_vote.html')


def seal(request):
    if request.method == 'POST':
        ballot = request.POST.get('ballot_input')
        vote_id = request.POST.get('vote-id')
        ballot_byte = ballot.encode('utf-8')
        ballot_hash = SHA3_256.new(ballot_byte).hexdigest()
        # Puzzle requirement: '0' * n (n leading zeros)
        puzzle, pcount = settings.PUZZLE, settings.PLENGTH
        nonce = 0

        block_transactions = Vote.objects.filter(id=vote_id).order_by('timestamp')

        # create Merkle hash
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in block_transactions], True)
        root.make_tree()
        merkle_hash = root.get_merkle_root()

        # Try to solve puzzle
        start_time = time.time()  # benchmark
        timestamp = _get_timestamp()  # mark the start of mining effort

        # get prev hash from prev block
        prev_hash = get_prev_block_hash()

        while True:
            block_hash = SHA3_256.new(("{}{}{}".format(ballot, nonce, timestamp).encode('utf-8'))).hexdigest()
            print('\ntrial hash: {}\n'.format(block_hash))
            if block_hash[:pcount] == puzzle:
                stop_time = time.time()
                print("\nblock is sealed in {} seconds\n".format(stop_time - start_time))
                break
            nonce += 1

        block = Block(prev_h=prev_hash, block_hash=block_hash, nonce=nonce, merkle_h=merkle_hash, timestamp=timestamp)
        block.save()

        # create block object

        context = {
            'prev_hash': prev_hash,
            'transaction_hash': ballot_hash,
            'nonce': nonce,
            'block_hash': block_hash,
            'timestamp': timestamp,
        }
        return render(request, 'seal.html', context)
    return redirect('/vote/')


def get_prev_block_hash():
    obj = Block.objects.last()
    if obj:
        return obj.block_hash
    else:
        return '0' * 64


def transactions(request):
    """See all transactions that have been contained in blocks."""
    vote_list = Vote.objects.all().order_by('timestamp')
    paginator = Paginator(vote_list, 100, orphans=20, allow_empty_first_page=True)

    page = request.GET.get('page')
    votes = paginator.get_page(page)

    hashes = [SHA3_256.new(str(v).encode('utf-8')).hexdigest() for v in votes]

    block_hashes = []
    # for i in range(0, len(votes)):
    #     try:
    #         block_obj = Block.objects.get(id=votes[i].block_id)
    #         block_hash = block_obj.block_hash
    #     except Exception as e:
    #         print(e)
    #         block_hash = 404
    #     block_hashes.append(block_hash)

    for vote in votes:
        try:
            block_obj = Block.objects.get(id=vote.block_id)
            block_hash = block_obj.block_hash
        except Exception as e:
            print(e)
            block_hash = 404
        block_hashes.append(block_hash)

    # zip the three iters
    votes_pg = votes  # for pagination
    votes = zip(votes, hashes, block_hashes)
    # votes = votes

    # Calculate the voting result of 3 cands, the ugly way
    result = []
    for i in range(0, 3):
        try:
            r = Vote.objects.filter(vote=i + 1).count()
        except:
            r = 0
        result.append(r)

    context = {
        'votes': votes,
        'result': result,
        'votes_pg': votes_pg,
    }
    return render(request, 'transactions.html', context)


def blockchain(request):
    """See all mined blocks."""
    blocks = Block.objects.all().order_by('id')
    context = {
        'blocks': blocks,
    }
    return render(request, 'blockchain.html', context)


def block_detail(request, block_hash):
    """See the details of a block and its transactions."""
    block = get_object_or_404(Block, block_hash=block_hash)
    # Select all corresponding transactions
    transaction_list = Vote.objects.filter(block_id=block.id).order_by('timestamp')
    paginator = Paginator(transaction_list, 100, orphans=20)

    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    transactions_hashes = [SHA3_256.new(str(t).encode('utf-8')).hexdigest() for t in transactions]

    transactions_pg = transactions  # for pagination
    transactions = zip(transactions, transactions_hashes)

    # Get prev and next block id
    prev_block = Block.objects.filter(id=block.id - 1).first()
    next_block = Block.objects.filter(id=block.id + 1).first()

    # Check the integrity of transactions
    root = MerkleTools()
    root.add_leaf([str(tx) for tx in transaction_list], True)
    root.make_tree()
    merkle_hash = root.get_merkle_root()
    tampered = block.merkle_h != merkle_hash

    context = {
        'bk': block,
        'transactions': transactions,
        'prev_block': prev_block,
        'next_block': next_block,
        'transactions_pg': transactions_pg,
        'tampered': tampered,
        'verified_merkle_hash': merkle_hash,
    }

    return render(request, 'block_details.html', context)


def sync_block(request, block_id):
    """Restore transactions of a block from honest node."""
    b = Block.objects.get(id=block_id)
    print('\nSyncing transactions in block {}\n'.format(b.id))
    # Get all existing transactions in this block and delete them
    Vote.objects.filter(block_id=block_id).delete()
    # Then rewrite from backup node
    bak_votes = VoteBackup.objects.filter(block_id=block_id).order_by('timestamp')
    for bv in bak_votes:
        v = Vote(id=bv.id, vote=bv.vote, user=bv.user, timestamp=bv.timestamp, block_id=bv.block_id)
        v.save()
    # Just in case, delete transactions without valid block
    block_count = Block.objects.all().count()
    Vote.objects.filter(block_id__gt=block_count).delete()
    Vote.objects.filter(block_id__lt=1).delete()
    print('\nSync complete\n')
    return redirect('/block/' + b.block_hash)


def verify(request):
    """Verify transactions in all blocks by re-calculating the merkle root."""

    print('verifying data...')
    number_of_blocks = Block.objects.all().count()
    corrupt_block_list = ''
    for i in range(1, number_of_blocks + 1):
        # Select block #i
        b = Block.objects.get(id=i)

        # Select all transactions in block #i
        transactions = Vote.objects.filter(block_id=i).order_by('timestamp')

        # Verify them
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()

        if b.merkle_h == merkle_h:
            message = 'Block {} verified.'.format(i)
        else:
            message = 'Block {} is TAMPERED'.format(i)
            corrupt_block_list += ' {}'.format(i)
        print('{}'.format(message))
    if len(corrupt_block_list) > 0:
        messages.warning(request, 'The following blocks have corrupted transactions: {}.'.format(corrupt_block_list),
                         extra_tags='bg-danger')
    else:
        messages.info(request, 'All transactions in blocks are intact.', extra_tags='bg-info')
    return redirect('/blockchain')


def sync(request):
    """Restore transactions from honest node."""
    deleted_old_votes = Vote.objects.all().delete()[0]
    print('\nTrying to sync {} transactions with 1 node(s)...\n'.format(deleted_old_votes))
    bk_votes = VoteBackup.objects.all().order_by('timestamp')
    for bk_v in bk_votes:
        vote = Vote(id=bk_v.id, vote=bk_v.vote, user=bk_v.user, timestamp=bk_v.timestamp, block_id=bk_v.block_id)
        vote.save()
    print('\nSync complete.\n')
    messages.info(request, 'All blocks have been synced successfully.')
    return redirect('/blockchain')


def _get_timestamp():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))
    # return datetime.datetime.now().timestamp()
