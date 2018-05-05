import numpy as np
import torch
import argparse
import pickle
from random import shuffle
from torch.autograd import Variable

from EmbedAlign import EmbedAlign
from preprocess import read_corpus, create_parallel_batches

parser = argparse.ArgumentParser()
parser.add_argument('--dims', type=int, default=100, help='Word vector dimensionality')
parser.add_argument('--batch', type=int, default=100, help='Batch size')
parser.add_argument('--epochs', type=int, default=30, help='Number of epochs to train.')
parser.add_argument('--lr', type=float, default=0.001, help='Initial learning rate.')
parser.add_argument('--test', type=int, default=None, help='Number of sentences to consider for testing')
parser.add_argument('--n_batches', type=int, default=None, help='Number of training batches')
# parser.add_argument('--save', type=str, default='skipgram-embeds.txt', help='Path of the output text file containing embeddings')


args = parser.parse_args()
embed_dim = args.dims
batch_size = args.batch
num_epochs = args.epochs
lr = args.lr
num_batches = args.n_batches
# output_path = args.save
print('Embedding dimensionality: {}'.format(embed_dim))
print('Batch size: {}'.format(batch_size))
print('Number of sentence pairs: {}'.format(batch_size * num_batches))
print('{} epochs. Initial learning rate: {}'.format(num_epochs, lr))

print('--- Load data ---')

# corpus_en, word2idx_en, _ = read_corpus('data/europarl/training.en', n_sentences=args.test)
# corpus_fr, word2idx_fr, _ = read_corpus('data/europarl/training.fr', n_sentences=args.test)

# batches_en, batches_fr = create_parallel_batches(corpus_en, corpus_fr, word2idx_en, word2idx_fr, batch_size=batch_size)

with open('w2i-europarl-en.p', 'rb') as f_in:
    word2idx_en = pickle.load(f_in)

with open('w2i-europarl-fr.p', 'rb') as f_in:
    word2idx_fr = pickle.load(f_in)

with open('embedalign-europarl-100btc.p', 'rb') as f_in:
    batches_en, batches_fr = pickle.load(f_in)

vocab_size_en = len(word2idx_en)
vocab_size_fr = len(word2idx_fr)

model = EmbedAlign(vocab_size_en,
                  vocab_size_fr,
                  embed_dim)

optimizer = torch.optim.Adam(model.parameters())

batches = list(zip(batches_en, batches_fr))
shuffle(batches)

if num_batches:
    batches = batches[:num_batches]

print('--- Train ---')

# Train
for epoch in range(1, num_epochs+1):

    overall_loss = 0
    model.train()
    optimizer.zero_grad()

    for batch_en, batch_fr in zip(batches_en[:1000], batches_fr[:1000]):

        batch_en = Variable(batch_en, requires_grad=False)
        batch_fr = Variable(batch_fr, requires_grad=False)

        loss = model(batch_en, batch_fr)

        overall_loss += loss.data[0]
        loss.backward()
        optimizer.step()

    # if epoch % 5 == 0:
    print('Loss at epoch {}: {}'.format(epoch, overall_loss / epoch))


torch.save(model.state_dict(), 'EmbedAlignModel-{}.p'.format(num_batches))


# # Write embeddings to file
# embeddings = model.input_embeds.weight

# with open(output_path, 'w') as f_out:
#     for idx in range(embeddings.size()[0]):
#         word = idx2word[idx]

#         embed = embeddings[idx, :]
#         embed = str(list(embed.data.numpy()))
#         embed = embed[1:-1]

#         print('{} {}'.format(word, embed), file=f_out)