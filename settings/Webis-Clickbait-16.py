def load_data(item_handle):
    import os
    import json
    import csv

    def load_annotations(path_truth, annotator):
        dict_annotations = {}
        with open(os.path.join(path_truth, annotator+'.csv'), 'r') as f:
            spamreader = csv.reader(f)
            for row in spamreader:
                id_tweet = int(row[0])
                score = row[1]
                dict_annotations[id_tweet] = score

        return dict_annotations

    path_corpora = '../corpora/webis-cbc-16'
    path_truth = os.path.join(path_corpora, 'truth')
    path_problems = os.path.join(path_corpora, 'problems')


    dict_annotations_annotatorA = load_annotations(path_truth, 'annotatorA')
    dict_annotations_annotatorB = load_annotations(path_truth, 'annotatorB')
    dict_annotations_annotatorC = load_annotations(path_truth, 'annotatorC')
    dict_annotations_majority = load_annotations(path_truth, 'majority')

    counter_error = 0
    for folder in os.listdir(path_problems):
        path_problem = os.path.join(path_problems, folder)
        for file in os.listdir(path_problem):
            path_file = os.path.join(path_problem, file)
            if file.endswith('.json'):
                with open(path_file, 'r') as f:
                    try:
                        obj_json = json.loads(f.read())
                        obj_tweet = {}
                        obj_tweet['id'] = obj_json['id']
                        obj_tweet['text'] = obj_json['text']
                        obj_tweet['retweet_count'] = int(obj_json['retweet_count'])
                        obj_tweet['annotatorA'] = dict_annotations_annotatorA[obj_json['id']]
                        obj_tweet['annotatorB'] = dict_annotations_annotatorB[obj_json['id']]
                        obj_tweet['annotatorC'] = dict_annotations_annotatorC[obj_json['id']]
                        obj_tweet['majority'] = dict_annotations_majority[obj_json['id']]
                        item_handle.add(obj_tweet)
                    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                        counter_error += 1

    print('counter_error')
    print(counter_error)
    print('counter_error')

# this is the main dictionary containing the necessary information to load and display your corpus
DICT_SETTINGS_VIEWER = {
    'name': 'Webis-Clickbait-16',
    'description': 'This corpus holds 2992 annotated Tweets.',
    'data_type': 'custom',
    'load_data_function': load_data,
    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'text': {
            'type': 'text',
            'display_name': 'Text'
        },
        'retweet_count': {
            'type': 'number',
            'display_name': 'Retweets'
        },
        'annotatorA': {
            'type': 'string',
            'display_name': 'A'
        },
        'annotatorB': {
            'type': 'string',
            'display_name': 'B'
        },
        'annotatorC': {
            'type': 'string',
            'display_name': 'C'
        },
        'majority': {
            'type': 'string',
            'display_name': 'majority'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'retweet_count', 'text', 'annotatorA', 'annotatorB', 'annotatorC', 'majority'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'text',
            'description': 'Tweet Text',
            'placeholder': 'Text Input',
            'default_value': '',
        },
        {
            'data_field': 'majority',
            'description': 'Majority',
            'placeholder': 'Text Input',
            'default_value': '',
        },
        {
            'data_field': 'retweet_count',
            'description': 'Count Retweets',
            'placeholder': 'Count Input',
            'default_value': '',
        },
    ],
    'secret_token': 'test',
    'template_html': """<style>
    .box_tweet {
        border: 1px solid #ddd;
        border-radius: 7px;
        padding: 30px 40px;
    }
    .box_color {
        height: 3rem;
        width: 3rem;
    }
</style>
<div class="row justify-content-center mt-5">
    <div class="col-lg-5 col-md-8 col-sm-10">
        <div class="box_tweet">
            <p id="text_tweet" style="font-size: 26px"></p>
            <div id="wrapper_images_'+tweet[0]+'" class="row"></div>
        </div>
    </div>
</div>
<div class="row justify-content-center mt-5">
    <div class="col col-md-auto">
        <div class="row text-nowrap">
            <div class="col">
                <div id="annotation_a" class="box_color mx-auto"></div>
                Annotator A
            </div>
            <div class="col">
                <div id="annotation_b" class="box_color mx-auto"></div>
                Annotator B
            </div>
            <div class="col">
                <div id="annotation_c" class="box_color mx-auto"></div>
                Annotator C
            </div>
            <div class="col">
                <div id="annotation_majority" class="box_color mx-auto"></div>
                Majority
            </div>
        </div>
    </div>
</div>

<script>
    function linkify(text){
        if (text) {
            text = text.replace(
                /((https?\:\/\/)|(www\.))(\S+)(\w{2,4})(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi,
                function(url){
                    var full_url = url;
                    if (!full_url.match('^https?:\/\/')) {
                        full_url = 'http://' + full_url;
                    }
                    return '<a href="' + full_url + '">' + 'Link' + '</a>';
                }
            );
        }
        return text;
    }

    function preprocess_text(text)
    {
        return linkify(text);
    }

    function get_color(annotation)
    {
        if(annotation == 'strong' || annotation == 'clickbait')
        {
            return "hsl(0,100%,50%)";
        } else if(annotation == 'medium') {
            return "hsl(40,100%,50%)";
        } else if(annotation == 'weak') {
            return "hsl(80,100%,50%)";
        } else if(annotation == 'none' || annotation == 'no-clickbait') {
            return "hsl(120,100%,50%)";
        }
        console.log('error')
    }

    $(document).ready(function()
    {
        console.log(obj_item)
        $('#text_tweet').html(preprocess_text(obj_item.text));
        $('#annotation_a').css('background-color', get_color(obj_item.annotatorA));
        $('#annotation_b').css('background-color', get_color(obj_item.annotatorB));
        $('#annotation_c').css('background-color', get_color(obj_item.annotatorC));
        $('#annotation_majority').css('background-color', get_color(obj_item.majority));
    });
</script>"""
    # 'template_path': '../corpora/webis-cbc-16/template.html'
}