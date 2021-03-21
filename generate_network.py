import json
import networkx as nx
import pickle
from pyvis.network import Network
import math
import random
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE

model = KeyedVectors.load(
    "/model/idwiki_word2vec_200_new_lower.model")


def generate_edges(word_tokens, similarity_threshold=0.5, save_edges_to_file=False):
    word_tokens = set(word_tokens)
    word_set_tuples = set()

    # IDEA : Set weight attributes of nodes

    while bool(word_tokens):
        main_word = word_tokens.pop()

        for check_word in word_tokens:
            try:
                sim = model.wv.similarity(main_word, check_word)
                if sim > 0.5:
                    word_set_tuples.add((main_word, check_word, sim))
                else:
                    continue
            except KeyError:
                continue

    if save_edges_to_file:
        with open("edges.pkl", "wb") as file:
            pickle.dump(word_set_tuples, file)

    return word_set_tuples


def create_graph_from_edges(edges, with_tsne=False):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    if with_tsne:
        for word, x, y in tsne_position(list(G.nodes)):
            G.nodes[word]['x'] = float(x)
            G.nodes[word]['y'] = float(y)

    return G


def tsne_position(vocab):
    word_list = []
    wordvecs = []

    for word in vocab:
        try:
            wordvecs.append(model[word])
            word_list.append(word)
        except KeyError:
            pass

    tsne_model = TSNE(perplexity=1, n_components=2,
                      init='pca', random_state=42)
    coordinates = tsne_model.fit_transform(wordvecs)
    x = []
    y = []
    for value in coordinates:
        x.append(value[0])
        y.append(value[1])
    return zip(word_list, x, y)


def color_connected_components(G):
    for cluster in nx.connected_components(G):
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        size = 5*math.log(len(cluster)) + 8
        for node in cluster:
            G.nodes[node]['color'] = color
            G.nodes[node]['size'] = size


def visualize_graph(graph, notebook=False):
    net = Network(notebook=notebook)
    net.width = '100%'
    net.from_nx(graph, edge_weight_transf=float)
    net.set_options("""
    var options = {
  "nodes": {
    "font": {
      "size": 40
    }
  }
}
""")
    net.show("word.html")


def main():
    G = create_graph_from_edges()
    color_connected_components(G)
    visualize_graph(G)


if __name__ == "__main__":
    main()
