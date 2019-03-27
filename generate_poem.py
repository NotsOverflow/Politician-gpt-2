import unicodedata, os, re, random, json, sys
import numpy as np
import tensorflow as tf
import model, sample, encoder

if len(sys.argv) < 2:
    exit("you must provide a word to get a poem")

FOLDER="eminem_clean"

mapping = {
 '\xa0': ' ',
 'Æ': 'AE',
 'æ': 'ae',
 'è': 'e',
 'é': 'e',
 'ë': 'e',
 'ö': 'o',
 '–': '-',
 '—': '-',
 '‘': "'",
 '’': "'",
 '“': '"',
 '”': '"'
}

def list_all_files(path):
    result = []
    for filename in os.listdir(path):
        result.append(filename)
    return result

model_name = '117M'
seed = None
nsamples = 10
batch_size = 10
length = 23
temperature = 0.8 # 0 is deterministic
top_k = 0 # 0 means no restrictions
the_sess = ""
assert nsamples % batch_size == 0

enc = encoder.get_encoder(model_name)
hparams = model.default_hparams()
with open(os.path.join('models', model_name, 'hparams.json')) as f:
    hparams.override_from_dict(json.load(f))

if length is None:
    length = hparams.n_ctx // 2
elif length > hparams.n_ctx:
    raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

def remove_special(text):
    return ''.join([mapping[e] if e in mapping else e for e in text])

def strip_word(word):
    word = re.sub('^\W*|\W*$', '', word).lower()
    return word
def titlecase_word(word):
    return word[0].upper() + word[1:]

def random_chunk(array, length):
    start = random.randint(0, max(0, len(array) - length - 1))
    return array[start:start+length]

def random_item(array):
    return array[random.randint(0, len(array) - 1)]

def clean(text):
    return text.split('<|endoftext|>')[0]

output = ""

def generate(inspiration, seed):
    print("generating for %s" % seed)
    inspiration = remove_special(inspiration).strip()
    seed = titlecase_word(seed).strip()

    raw_text = inspiration + '\n' + seed
    context_tokens = enc.encode(raw_text)
    n_context = len(context_tokens)

    temp = []
    results = []
    for index in range(nsamples // batch_size):
        print("run %s" % index)
        out = the_sess.run(output, feed_dict={
            context: [context_tokens for _ in range(batch_size)]
        })
        for sample in out:
            text = enc.decode(sample[n_context:])
            temp = seed + text
            temp = temp.split("\n")
            for line in temp:
                if len(line) > 3:
                    results.append(line)
    
    return "\n".join(results)



#sess = tf.InteractiveSession()
with tf.Session(graph=tf.Graph()) as sess:
    the_sess = sess
    context = tf.placeholder(tf.int32, [batch_size, None])
    np.random.seed(seed)
    tf.set_random_seed(seed)

    output = sample.sample_sequence(
        hparams=hparams, length=length,
        context=context,
        batch_size=batch_size,
        temperature=temperature, top_k=top_k
    )

    saver = tf.train.Saver()
    ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
    saver.restore(the_sess, ckpt)


    basenames = []
    all_poems = {}
    total_lines = 0
    #words = set()
    for fn in list_all_files(FOLDER):
        with open("%s/%s" % (FOLDER, fn)) as f:
            print("appending %s" % fn)
            basenames.append(fn)
            poem = f.read()
            all_poems[fn] = poem.split("\n")
            total_lines += len(poem)
            #words.update([strip_word(e) for e in poem.split()])
    #words.remove('')
    #words = list(words)
            
    print(total_lines)

    print(basenames)
    #print(words)
    #print(random_chunk(all_poems[basenames[0]], 2), titlecase_word(random_item(words)))

    seed = sys.argv[1]

    inspiration_lines = 16

    all_results = {}
    print(seed)
    inspiration = []
    for text in all_poems:
        for line in text:
            if line != "":
                inspiration.append(line)
    inspiration = '\n'.join(random_chunk(inspiration,inspiration_lines))
    result = generate(inspiration, titlecase_word(seed))
    print(result)

        
    with open('generated.json', 'w') as f:
        json.dump(result, f, separators=(',', ':'))


