import numpy as np


def dangerous_false_real_rate(y_true, probabilities):
    synthetic = np.asarray(y_true) != 0
    return float((np.asarray(probabilities)[synthetic].argmax(1) == 0).mean()) if synthetic.any() else float("nan")


def multiclass_brier(y_true, probabilities):
    target = np.eye(3)[np.asarray(y_true)]
    return float(np.mean(np.sum((np.asarray(probabilities) - target) ** 2, axis=1)))


def coverage_selective_risk(y_true, probabilities, reliability, coverages=(1, .9, .8, .7, .5)):
    y_true, probabilities = np.asarray(y_true), np.asarray(probabilities)
    order = np.argsort(-np.asarray(reliability).reshape(-1), kind="stable")
    return [{"coverage": c, "count": len(keep),
             "selective_risk": float((probabilities[keep].argmax(1) != y_true[keep]).mean())}
            for c in coverages for keep in [order[:max(1, round(len(order) * c))]]]


def binary_auc(y_true, scores):
    y=np.asarray(y_true).astype(int); scores=np.asarray(scores); pos=y.sum(); neg=len(y)-pos
    if not pos or not neg: return float("nan")
    order=np.argsort(scores, kind="stable"); ranks=np.empty(len(y),float); ranks[order]=np.arange(1,len(y)+1)
    for value in np.unique(scores):
        tied=np.flatnonzero(scores==value); ranks[tied]=ranks[tied].mean()
    return float((ranks[y==1].sum()-pos*(pos+1)/2)/(pos*neg))


def average_precision(y_true, scores):
    y=np.asarray(y_true).astype(int); order=np.argsort(-np.asarray(scores),kind="stable"); y=y[order]
    if not y.sum(): return float("nan")
    precision=np.cumsum(y)/(np.arange(len(y))+1)
    return float((precision*y).sum()/y.sum())


def unseen_generator_metrics(y_true, probabilities, generators):
    y_true=np.asarray(y_true); probabilities=np.asarray(probabilities); binary=(y_true==1).astype(int)
    score=probabilities[:,1]; predicted=(score>=.5).astype(int)
    recalls={}
    for generator in sorted(set(generators)):
        mask=(np.asarray(generators)==generator)&(binary==1)
        if mask.any(): recalls[str(generator)]=float(predicted[mask].mean())
    real_recall=float((predicted[binary==0]==0).mean()) if (binary==0).any() else float("nan")
    ai_recall=float(predicted[binary==1].mean()) if binary.any() else float("nan")
    return {"roc_auc":binary_auc(binary,score),"pr_auc":average_precision(binary,score),
            "balanced_accuracy":(real_recall+ai_recall)/2,"real_recall":real_recall,
            "ai_generated_recall":ai_recall,"per_generator_recall":recalls}
